import json

# ===== DIET RECOMMENDATION SYSTEM =====

DIET_DATABASE = {
    'Lose Weight': {
        'Low': {
            'reason': 'You have a sedentary lifestyle and want to lose weight. This calorie-controlled diet helps you achieve gradual, sustainable weight loss.',
            'breakfast': 'Oatmeal with berries and almonds (300 cal) | Greek yogurt with honey | Green tea',
            'lunch': 'Grilled chicken breast (150g) with steamed broccoli and brown rice (1 cup) | Salad with olive oil dressing',
            'snacks': 'Apple with almond butter | Carrots and hummus | Green smoothie with spinach and banana',
            'dinner': 'Baked salmon (150g) with sweet potato and asparagus | Lentil soup',
            'swaps': [
                ['White rice', 'Brown rice or quinoa'],
                ['Fried chicken', 'Grilled or baked chicken'],
                ['Regular milk', 'Low-fat or almond milk'],
                ['Sugary drinks', 'Water, green tea, or black coffee'],
                ['Butter', 'Olive oil or coconut oil']
            ]
        },
        'Medium': {
            'reason': 'You have moderate activity and want sustainable weight loss. This balanced diet supports your fitness goals while maintaining energy.',
            'breakfast': 'Whole wheat toast with avocado and poached eggs | Orange juice',
            'lunch': 'Turkey sandwich on whole wheat with vegetables | Mixed salad with chickpeas',
            'snacks': 'Greek yogurt with granola | Banana with protein powder smoothie | Mixed nuts (handful)',
            'dinner': 'Lean ground turkey (150g) with zucchini noodles and marinara sauce | Roasted vegetables',
            'swaps': [
                ['White bread', 'Whole wheat or multigrain'],
                ['Full-fat dairy', 'Low-fat alternatives'],
                ['Soft drinks', 'Coconut water or herbal tea'],
                ['Processed snacks', 'Nuts and seeds'],
                ['Mayonnaise', 'Greek yogurt']
            ]
        },
        'High': {
            'reason': 'You are very active and need proper nutrition for weight loss. This protein-rich diet supports muscle recovery while creating a calorie deficit.',
            'breakfast': 'Protein pancakes with berries | Scrambled eggs with whole wheat toast | Coffee with almond milk',
            'lunch': 'Grilled chicken breast (200g) with quinoa and roasted vegetables | Mixed leaf salad',
            'snacks': 'Protein shake | Apple with almond butter | Hard-boiled eggs | Cottage cheese with berries',
            'dinner': 'Grilled fish (200g) with sweet potato and green beans | Vegetable stir-fry',
            'swaps': [
                ['Refined carbs', 'Complex carbohydrates'],
                ['High-fat meat', 'Lean protein'],
                ['Processed foods', 'Whole foods'],
                ['Sweet desserts', 'Protein-based alternatives'],
                ['Regular pasta', 'Lentil or chickpea pasta']
            ]
        }
    },
    'Gain Weight': {
        'Low': {
            'reason': 'You are underweight and have low activity. This calorie-surplus diet helps you gain healthy weight with nutritious, energy-dense foods.',
            'breakfast': 'Whole grain pancakes with peanut butter and banana | Full-fat milk with almonds',
            'lunch': 'Pasta with meat sauce and cheese | Whole wheat bread | Butter | Full-fat milk',
            'snacks': 'Peanut butter sandwich | Trail mix | Cheese and crackers | Protein bar',
            'dinner': 'Beef steak (200g) with mashed potatoes (butter & cream) | Vegetables with olive oil',
            'swaps': [
                ['Water', 'Full-fat milk, juices, or smoothies'],
                ['Lean meat', 'Meat with healthy fats'],
                ['Diet products', 'Full-fat alternatives'],
                ['Plain rice', 'Rice with butter or oil'],
                ['Air-fried foods', 'Fried or oil-cooked foods']
            ]
        },
        'Medium': {
            'reason': 'You are underweight with moderate activity. This nutrient-dense diet supports healthy weight gain and muscle development.',
            'breakfast': 'Oats with whole milk, nuts, and dates | Boiled eggs (3) | Orange juice',
            'lunch': 'Chicken with fried rice, vegetables cooked in oil | Mango or banana',
            'snacks': 'Protein shake with whole milk | Nuts and seeds | Cheese sandwich | Smoothie bowl',
            'dinner': 'Fish or mutton (200g) with dal and butter rice | Vegetable curry with ghee',
            'swaps': [
                ['Skimmed milk', 'Whole milk (3% fat)'],
                ['Steamed foods', 'Cooked in oil or butter'],
                ['Low-calorie snacks', 'Energy bars and nuts'],
                ['Lean cuts', 'Fattier cuts of meat'],
                ['Unsweetened drinks', 'Sweet juices and shakes']
            ]
        },
        'High': {
            'reason': 'You are active but underweight. This high-calorie, protein-rich diet supports muscle gain and athletic performance.',
            'breakfast': 'Protein pancakes with honey and almonds | Whole milk | Boiled eggs (2)',
            'lunch': 'Grilled chicken (250g) with brown rice and ghee | Beans and vegetables',
            'snacks': 'Protein shake with banana | Peanut butter sandwich | Nuts mix | Cheese and crackers',
            'dinner': 'Lean meat or fish (250g) with sweet potato (cooked in butter) | Salad with olive oil',
            'swaps': [
                ['Water', 'Full-fat milk, protein shakes, fresh juice'],
                ['Boiled eggs', 'Scrambled or fried'],
                ['No oil cooking', 'Generous oil/butter use'],
                ['Plain carbs', 'Carbs with healthy fats'],
                ['Low-calorie snacks', 'Calorie-dense snacks']
            ]
        }
    },
    'Maintain Weight': {
        'Low': {
            'reason': 'You want to maintain your current weight with low activity. This balanced diet ensures stable weight and good health.',
            'breakfast': 'Whole grain toast with butter and jam | Eggs (2) | Tea with milk',
            'lunch': 'Grilled chicken (150g) with rice and vegetables | Fruit juice',
            'snacks': 'Banana | Yogurt | Granola bar | Tea with biscuits',
            'dinner': 'Fish or lean meat (150g) with vegetables and rice | Salad',
            'swaps': [
                ['Sugary cereals', 'Whole grain cereals'],
                ['Fried snacks', 'Baked snacks'],
                ['Soft drinks', 'Water or herbal tea'],
                ['Excessive oil', 'Measured amounts of healthy oil'],
                ['White rice', 'Brown rice (50% of the time)']
            ]
        },
        'Medium': {
            'reason': 'You have moderate activity and want to maintain weight. This balanced diet supports your active lifestyle.',
            'breakfast': 'Oatmeal with berries | Whole wheat toast with avocado | Tea or coffee',
            'lunch': 'Grilled chicken (150g) with brown rice and vegetables | Mixed salad',
            'snacks': 'Apple with almond butter | Greek yogurt | Protein bar',
            'dinner': 'Lean meat (150g) with sweet potato and green vegetables | Light soup',
            'swaps': [
                ['All white carbs', '50% whole grains'],
                ['Sugary items', 'Natural sweets'],
                ['Trans fats', 'Unsaturated fats'],
                ['Processed meat', 'Fresh meat'],
                ['Creamy sauces', 'Oil-based or tomato sauces']
            ]
        },
        'High': {
            'reason': 'You are very active and need proper nutrition to maintain weight. This diet supports your fitness while maintaining calorie balance.',
            'breakfast': 'Protein oatmeal with berries and nuts | Eggs | Green juice',
            'lunch': 'Grilled chicken (180g) with quinoa and vegetables | Mixed salad with seeds',
            'snacks': 'Protein shake | Banana with nut butter | Greek yogurt with granola',
            'dinner': 'Fish (180g) with brown rice and steamed vegetables | Vegetable stir-fry',
            'swaps': [
                ['Low protein', 'High protein options'],
                ['Simple carbs', 'Complex carbs'],
                ['Sugary drinks', 'Protein shakes or water'],
                ['Low-fat dairy', 'Full-fat or Greek dairy'],
                ['Fried foods', 'Baked or grilled']
            ]
        }
    },
    'Improve Fitness': {
        'Low': {
            'reason': 'You want to improve fitness with low current activity. This nutrient-rich diet will give you energy to start exercising.',
            'breakfast': 'Whole grain toast with peanut butter | Orange juice | Oatmeal with berries',
            'lunch': 'Grilled chicken (130g) with brown rice and vegetables | Fruit',
            'snacks': 'Apple | Almonds | Yogurt | Smoothie',
            'dinner': 'Lean meat (130g) with sweet potato and broccoli | Soup',
            'swaps': [
                ['White bread', 'Whole wheat bread'],
                ['Regular pasta', 'Whole wheat pasta'],
                ['Sugary drinks', 'Fresh fruit juice or water'],
                ['Fried foods', 'Grilled or baked foods'],
                ['Butter', 'Olive oil']
            ]
        },
        'Medium': {
            'reason': 'You have moderate activity and want to improve fitness. This protein-focused diet supports muscle development.',
            'breakfast': 'Protein pancakes | Eggs (2) | Green tea | Berries',
            'lunch': 'Grilled chicken (160g) with brown rice and vegetables | Salad with olive oil',
            'snacks': 'Protein shake | Greek yogurt | Banana with almond butter',
            'dinner': 'Fish or lean meat (160g) with sweet potato and green beans | Stir-fry vegetables',
            'swaps': [
                ['Regular dairy', 'Greek yogurt or protein dairy'],
                ['Refined carbs', 'Complex carbohydrates'],
                ['Low protein snacks', 'Protein bars or shakes'],
                ['Sugary foods', 'Natural alternatives'],
                ['High-calorie drinks', 'Water or black coffee']
            ]
        },
        'High': {
            'reason': 'You are very active and focused on fitness. This optimized diet maximizes performance and recovery.',
            'breakfast': 'Protein oatmeal with banana and nuts | Eggs (3) | Green juice',
            'lunch': 'Grilled chicken (200g) with quinoa and vegetables | Mixed salad with seeds',
            'snacks': 'Protein shake | Greek yogurt with berries | Hard-boiled eggs | Trail mix',
            'dinner': 'Fish or lean meat (200g) with brown rice and steamed vegetables | Vegetable curry',
            'swaps': [
                ['Low protein', 'High-protein alternatives'],
                ['Simple carbs', 'Complex carbs'],
                ['Regular milk', 'Protein milk or Greek yogurt'],
                ['Sugary items', 'Protein-based alternatives'],
                ['Processed foods', 'Whole, unprocessed foods']
            ]
        }
    }
}

MEDICAL_WARNINGS = {
    'Diabetes': '⚠️ Diabetes Warning: Avoid sugary foods and refined carbohydrates. Focus on low glycemic index foods. Consult your doctor before making dietary changes.',
    'BP': '⚠️ Blood Pressure Warning: Reduce sodium intake. Avoid processed foods and excess salt. Include potassium-rich foods like bananas and leafy greens.',
    'Thyroid': '⚠️ Thyroid Warning: Include iodine-rich foods. Avoid excessive cruciferous vegetables. Take supplements only after consulting your doctor.',
    'Cholesterol': '⚠️ High Cholesterol Warning: Reduce saturated fats and trans fats. Focus on soluble fiber from oats and beans. Include omega-3 fatty acids.'
}

def get_diet_plan(profile):
    """Get personalized diet plan based on profile"""
    goal = profile.get('goal', 'Maintain Weight')
    activity = profile.get('activity_level', 'Medium')
    
    # Get base diet plan
    if goal in DIET_DATABASE and activity in DIET_DATABASE[goal]:
        diet = DIET_DATABASE[goal][activity].copy()
    else:
        diet = DIET_DATABASE['Maintain Weight']['Medium'].copy()
    
    # Add medical warnings
    conditions = json.loads(profile.get('medical_conditions', '[]'))
    warnings = []
    for condition in conditions:
        if condition in MEDICAL_WARNINGS:
            warnings.append(MEDICAL_WARNINGS[condition])
    
    diet['warnings'] = ' '.join(warnings) if warnings else 'No specific medical warnings.'
    diet['goal'] = goal
    diet['activity'] = activity
    
    return diet
